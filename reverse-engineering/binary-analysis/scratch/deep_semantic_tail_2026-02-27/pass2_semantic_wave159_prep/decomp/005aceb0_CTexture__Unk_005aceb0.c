/* address: 0x005aceb0 */
/* name: CTexture__Unk_005aceb0 */
/* signature: uint __stdcall CTexture__Unk_005aceb0(int param_1, int param_2, int param_3, int param_4, int param_5) */


uint CTexture__Unk_005aceb0(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;

  if (param_3 < param_5) {
    iVar3 = CTexture__Helper_005acd90((void *)param_1,param_2,param_3,param_5);
    if (iVar3 == 0) {
      return 0xffffffff;
    }
    param_2 = *(uint *)(param_1 + 8);
    param_3 = *(int *)(param_1 + 0xc);
  }
  iVar3 = param_3 - param_5;
  uVar4 = param_2 >> ((byte)iVar3 & 0x1f) & (1 << ((byte)param_5 & 0x1f)) - 1U;
  if (*(int *)(param_4 + param_5 * 4) < (int)uVar4) {
    do {
      if (iVar3 < 1) {
        iVar3 = CTexture__Helper_005acd90((void *)param_1,param_2,iVar3,1);
        if (iVar3 == 0) {
          return 0xffffffff;
        }
        param_2 = *(uint *)(param_1 + 8);
        iVar3 = *(int *)(param_1 + 0xc);
      }
      iVar3 = iVar3 + -1;
      uVar4 = uVar4 << 1 | param_2 >> ((byte)iVar3 & 0x1f) & 1U;
      iVar1 = param_5 * 4;
      param_5 = param_5 + 1;
    } while (*(int *)(param_4 + 4 + iVar1) < (int)uVar4);
  }
  *(int *)(param_1 + 8) = param_2;
  *(int *)(param_1 + 0xc) = iVar3;
  if (param_5 < 0x11) {
    return (uint)*(byte *)(*(int *)(param_4 + 0x48 + param_5 * 4) + *(int *)(param_4 + 0x8c) + 0x11
                          + uVar4);
  }
  piVar2 = *(int **)(param_1 + 0x10);
  iVar3 = *piVar2;
  *(undefined4 *)(iVar3 + 0x14) = 0x76;
  (**(code **)(iVar3 + 4))(piVar2,0xffffffff);
  return 0;
}
