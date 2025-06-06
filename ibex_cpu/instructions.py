from dataclasses import dataclass
from enum import Enum
import unittest


class Cov(Enum):
    """Coverage Types

    Instruction Coverpoints:
      seen: Has been observed.
      zero_dst: The destination register has been `x0`.
      zero_src: A source register has been `x0`.
      same_src: Two source registers have been the same.
      br_backwards: Has caused a branch backwards.
      br_forwards: Has caused a branch forwards.

    Cross Instruction Coverpoints:
      raw_hazard: Reads from  a register the previous instruction wrote to.
    """

    SEEN = "seen"
    ZERO_DST = "zero_dst"
    ZERO_SRC = "zero_src"
    SAME_SRC = "same_src"
    BR_BACKWARDS = "br_backwards"
    BR_FORWARDS = "br_forwards"
    RAW_HAZARD = "raw_hazard"


class Instr(Enum):
    ADD = "add"
    SUB = "sub"
    SLL = "sll"
    SLT = "slt"
    SLTU = "sltu"
    XOR = "xor"
    SRL = "srl"
    SRA = "sra"
    OR = "or"
    AND = "and"
    SB = "sb"
    SH = "sh"
    SW = "sw"
    JAL = "jal"

    def type(self) -> type["TypedInstruction"]:
        # R-type instructions
        if self in {
            Instr.ADD, Instr.SUB, Instr.SLL, Instr.SLT, Instr.SLTU,
            Instr.XOR, Instr.SRL, Instr.SRA, Instr.OR,  Instr.AND
        }:
            return RInstruction

        # S-type store instructions
        elif self in {Instr.SB, Instr.SH, Instr.SW}:
            return SInstruction

        # J-type jump instruction
        elif self is Instr.JAL:
            return JInstruction

        # Fallback for unrecognized opcodes
        else:
            raise ValueError(f"Unrecognized instruction: {self!r}")



@dataclass(frozen=True)
class Encoding:
    encoding: int

    def typed(self) -> "TypedInstruction | None":
        opcode = self.encoding & 0x7F

        if opcode == 0b0110011:
            return RInstruction(self.encoding)
        elif opcode == 0b1101111:
            return JInstruction(self.encoding)
        elif opcode == 0b0100011:
            return SInstruction(self.encoding)
        else:
            return None



def get_rd(enc: Encoding) -> int:
    return (enc.encoding >> 7) & 0x1F


def get_rs1(enc: Encoding) -> int:
    return (enc.encoding >> 15) & 0x1F


def get_rs2(enc: Encoding) -> int:
    return (enc.encoding >> 20) & 0x1F


class RInstruction(Encoding):
    rd = get_rd
    rs1 = get_rs1
    rs2 = get_rs2

    def instruction(self) -> Instr:
        masked = self.encoding & 0xFE007000

        if masked == 0x00000000:
            return Instr.ADD
        elif masked == 0x40000000:
            return Instr.SUB
        elif masked == 0x00001000:
            return Instr.SLL
        elif masked == 0x00002000:
            return Instr.SLT
        elif masked == 0x00003000:
            return Instr.SLTU
        elif masked == 0x00004000:
            return Instr.XOR
        elif masked == 0x00005000:
            return Instr.SRL
        elif masked == 0x40005000:
            return Instr.SRA
        elif masked == 0x00006000:
            return Instr.OR
        elif masked == 0x00007000:
            return Instr.AND
        else:
            raise AssertionError("Invalid Instruction")


    @staticmethod
    def coverpoints() -> list[Cov]:
        return [Cov.SEEN, Cov.ZERO_DST, Cov.ZERO_SRC, Cov.SAME_SRC]

    def sample_coverage(self) -> list[Cov]:
        out = [Cov.SEEN]
        if 0 == self.rd():
            out.append(Cov.ZERO_DST)
        if self.rs1() == self.rs2():
            out.append(Cov.SAME_SRC)
        if 0 == self.rs1() or 0 == self.rs2():
            out.append(Cov.ZERO_SRC)
        return out

    @staticmethod
    def cross_coverpoints() -> list[tuple[Instr, Cov]]:
        return [
            (instr, Cov.RAW_HAZARD)
            for instr in Instr
            if instr.type() in {RInstruction, JInstruction}
        ]

    def sample_cross_coverage(
        self, previous: "TypedInstruction"
    ) -> list[tuple[Instr, Cov]]:
        out = []
        if isinstance(previous, RInstruction) or isinstance(previous, JInstruction):
            if previous.rd() in {self.rs1(), self.rs2()}:
                out.append((previous.instruction(), Cov.RAW_HAZARD))
        return out


class JInstruction(Encoding):
    rd = get_rd

    def instruction(self) -> Instr:
        return Instr.JAL

    def offset(self) -> int:
        """Inefficient and verbose extraction of offset."""
        e = self.encoding
        imm10_01 = (e >> 21) & 0x3FF
        imm11_11 = (e >> 20) & 0b1
        imm19_12 = (e >> 12) & 0xFF
        imm20_20 = (e >> 31) & 0b1
        imm = (imm10_01 << 1) | (imm11_11 << 11) | (imm19_12 << 12) | (imm20_20 << 20)
        if imm20_20:
            imm -= 1 << 21
        return imm

    @staticmethod
    def coverpoints() -> list[Cov]:
        return [Cov.SEEN, Cov.ZERO_DST, Cov.BR_BACKWARDS, Cov.BR_FORWARDS]

    def sample_coverage(self) -> list[Cov]:
        out = [Cov.SEEN]
        if 0 == self.rd():
            out.append(Cov.ZERO_DST)
        if 0 > self.offset():
            out.append(Cov.BR_BACKWARDS)
        if 0 < self.offset():
            out.append(Cov.BR_FORWARDS)
        return out

    @staticmethod
    def cross_coverpoints() -> list[tuple[Instr, Cov]]:
        return []

    def sample_cross_coverage(
        self, previous: "TypedInstruction"
    ) -> list[tuple[Instr, Cov]]:
        return []


class SInstruction(Encoding):
    rs1 = get_rs1
    rs2 = get_rs2

    def instruction(self) -> Instr:
        masked = self.encoding & 0x00007000

        if masked == 0x00000000:
            return Instr.SB
        elif masked == 0x00001000:
            return Instr.SH
        elif masked == 0x00002000:
            return Instr.SW
        else:
            raise AssertionError("Invalid Instruction")


    def offset(self) -> int:
        """Inefficient and verbose extraction of offset."""
        e = self.encoding
        imm04_00 = (e >> 7) & 0x1F
        imm11_05 = (e >> 25) & 0x7F
        imm = imm04_00 | (imm11_05 << 5)
        if imm >> 11:
            imm -= 1 << 12
        return imm

    @staticmethod
    def coverpoints() -> list[Cov]:
        return [Cov.SEEN, Cov.ZERO_SRC, Cov.SAME_SRC]

    def sample_coverage(self) -> list[Cov]:
        out = [Cov.SEEN]
        if self.rs1() == self.rs2():
            out.append(Cov.SAME_SRC)
        if 0 == self.rs1() or 0 == self.rs2():
            out.append(Cov.ZERO_SRC)
        return out

    @staticmethod
    def cross_coverpoints() -> list[tuple[Instr, Cov]]:
        return [
            (instr, Cov.RAW_HAZARD)
            for instr in Instr
            if instr.type() in {RInstruction, JInstruction}
        ]
        return []

    def sample_cross_coverage(
        self, previous: "TypedInstruction"
    ) -> list[tuple[Instr, Cov]]:
        out = []
        if isinstance(previous, RInstruction) or isinstance(previous, JInstruction):
            if previous.rd() in {self.rs1(), self.rs2()}:
                out.append((previous.instruction(), Cov.RAW_HAZARD))
        return out

from typing import Union
TypedInstruction = Union[RInstruction, JInstruction, SInstruction]


class TestInstructions(unittest.TestCase):
    def test_r_type(self) -> None:
        instr = [
            (0x00000033, "add", 0, 0, 0),
            (0x01EE12B3, "sll", 5, 28, 30),
            (0x40678633, "sub", 12, 15, 6),
        ]
        for (enc, name, rd, rs1, rs2) in instr:
            i = Encoding(enc).typed()
            self.assertIsInstance(i, RInstruction)
            assert isinstance(i, RInstruction)
            self.assertEqual(name, i.instruction().value)
            self.assertEqual(rd, i.rd())
            self.assertEqual(rs1, i.rs1())
            self.assertEqual(rs2, i.rs2())

    def test_j_type(self) -> None:
        instr = [
            (0xC1CFA2EF, "jal", 5, -23524),
            (0x1D2010EF, "jal", 1, 4562),
        ]
        for (enc, name, rd, offset) in instr:
            i = Encoding(enc).typed()
            self.assertIsInstance(i, JInstruction)
            assert isinstance(i, JInstruction)
            self.assertEqual(name, i.instruction().value)
            self.assertEqual(rd, i.rd())
            self.assertEqual(offset, i.offset())

    def test_s_type(self) -> None:
        instr = [
            (0xFC532F23, "sw", 6, 5, -34),
            (0x3AAE1223, "sh", 28, 10, 932),
            (0xC4388E23, "sb", 17, 3, -932),
        ]
        for (enc, name, rs1, rs2, offset) in instr:
            i = Encoding(enc).typed()
            self.assertIsInstance(i, SInstruction)
            assert isinstance(i, SInstruction)
            self.assertEqual(name, i.instruction().value)
            self.assertEqual(rs1, i.rs1())
            self.assertEqual(rs2, i.rs2())
            self.assertEqual(offset, i.offset())


if __name__ == "__main__":
    unittest.main()
