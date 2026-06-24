/* address: 0x0056468c */
/* name: CTexture__Unk_0056468c */
/* signature: double CTexture__Unk_0056468c(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

double CTexture__Unk_0056468c(void)

{
  uint uVar1;
  float10 in_ST0;
  float10 extraout_ST0;
  float10 fVar2;
  float10 extraout_ST0_00;
  float10 in_ST1;
  int iVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 in_stack_ffffffd6;
  undefined2 uStack_14;

  uStack_14 = (ushort)((unkuint10)in_ST0 >> 0x40);
  uVar1 = (uint)((unkuint10)in_ST1 >> 0x20);
  if (((uint)((unkuint10)in_ST1 >> 0x30) & 0x7fff0000) != 0) {
    CTexture__Unk_00564486
              (SUB104(in_ST1,0),uVar1,CONCAT22(in_stack_ffffffd6,(short)((unkuint10)in_ST1 >> 0x40))
              );
    return (double)extraout_ST0;
  }
  if (SUB104(in_ST1,0) != 0 || uVar1 != 0) {
    if ((uStack_14 & 0x7fff) < 0x7fbf) {
      fVar2 = in_ST1 * (float10)_DAT_00653ae4;
      iVar3 = SUB104(fVar2,0);
      uVar4 = (undefined2)((unkuint10)fVar2 >> 0x20);
      uVar5 = (undefined2)((unkuint10)fVar2 >> 0x30);
      uVar6 = (undefined2)((unkuint10)fVar2 >> 0x40);
    }
    else {
      fVar2 = in_ST1 * (float10)_DAT_00653ae4;
      iVar3 = SUB104(fVar2,0);
      uVar4 = (undefined2)((unkuint10)fVar2 >> 0x20);
      uVar5 = (undefined2)((unkuint10)fVar2 >> 0x30);
      uVar6 = (undefined2)((unkuint10)fVar2 >> 0x40);
    }
    CTexture__Unk_00564486(iVar3,CONCAT22(uVar5,uVar4),CONCAT22(in_stack_ffffffd6,uVar6));
    return (double)extraout_ST0_00;
  }
  return (double)(in_ST0 - (in_ST0 / in_ST1) * in_ST1);
}
