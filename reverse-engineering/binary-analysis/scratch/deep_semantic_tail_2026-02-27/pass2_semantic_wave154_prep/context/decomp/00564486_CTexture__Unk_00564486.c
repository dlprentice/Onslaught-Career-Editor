/* address: 0x00564486 */
/* name: CTexture__Unk_00564486 */
/* signature: int __cdecl CTexture__Unk_00564486(int param_1, uint param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CTexture__Unk_00564486(int param_1,uint param_2,int param_3)

{
  int in_EAX;
  int iVar1;
  float10 fVar2;
  float10 fVar3;
  undefined4 in_stack_0000001c;
  undefined2 in_stack_00000020;
  undefined2 in_stack_00000022;
  ushort in_stack_00000024;

  if ((((((CONCAT22((ushort)param_3,param_2._2_2_) ^ 0x700) & 0x700) == 0) &&
       ((&DAT_00653acc)[(param_2._2_2_ & 0x7800) >> 0xb] != '\0')) &&
      ((param_3 & 0x7fffU) != 0x7fff)) &&
     ((((in_stack_00000024 & 0x7fff) != 0 && ((in_stack_00000024 & 0x7fff) != 0x7fff)) &&
      (((CONCAT22(in_stack_00000022,in_stack_00000020) & 0x7fffffff) == 0 &&
       ((param_2 & 0x7fffffff) == 0)))))) {
    if ((param_3 & 0x7fffU) + 0x3f < (in_stack_00000024 & 0x7fff)) {
      iVar1 = ((in_stack_00000024 & 0x7fff) - (param_3 & 0x7fffU) & 0x3f | 0x20) + 1;
      param_3._0_2_ = in_stack_00000024 & 0x7fff | (ushort)param_3 & 0x8000;
      fVar3 = ABS((float10)CONCAT28((ushort)param_3,
                                    CONCAT26(param_2._2_2_,CONCAT24((undefined2)param_2,param_1))));
      fVar2 = ABS((float10)CONCAT28(in_stack_00000024,
                                    CONCAT26(in_stack_00000022,
                                             CONCAT24(in_stack_00000020,in_stack_0000001c))));
      do {
        if (fVar3 <= fVar2) {
          fVar2 = fVar2 - fVar3;
        }
        fVar3 = fVar3 * (float10)_DAT_00653afc;
        iVar1 = iVar1 + -1;
      } while (iVar1 != 0);
    }
    else {
      while (-1 < (int)((in_stack_00000024 & 0x7fff) - ((param_3 & 0x7fffU) + 10))) {
        fVar2 = (float10)CONCAT28(in_stack_00000024,
                                  CONCAT26(in_stack_00000022,
                                           CONCAT24(in_stack_00000020,in_stack_0000001c)));
        fVar3 = (float10)CONCAT28((in_stack_00000024 & 0x7fff) -
                                  ((in_stack_00000024 & 0x7fff) - (ushort)param_3 & 7 | 4) |
                                  (ushort)param_3 & 0x8000,
                                  CONCAT26(param_2._2_2_,CONCAT24((undefined2)param_2,param_1)));
        fVar2 = fVar2 - (fVar2 / fVar3) * fVar3;
        in_stack_0000001c = SUB104(fVar2,0);
        in_stack_00000020 = (undefined2)((unkuint10)fVar2 >> 0x20);
        in_stack_00000022 = (undefined2)((unkuint10)fVar2 >> 0x30);
        in_stack_00000024 = (ushort)((unkuint10)fVar2 >> 0x40);
      }
    }
  }
  return in_EAX;
}
