/* address: 0x0055d90b */
/* name: CDXTexture__Helper_0055d90b */
/* signature: int __cdecl CDXTexture__Helper_0055d90b(int param_1, int param_2, int param_3, void * param_4, void * param_5) */


int __cdecl
CDXTexture__Helper_0055d90b(int param_1,int param_2,int param_3,void *param_4,void *param_5)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;

  uVar5 = *(uint *)(param_1 + 0xc);
  iVar1 = *(int *)(param_1 + 0x10);
  uVar4 = uVar5;
  uVar3 = uVar5;
  while (uVar2 = uVar4, -1 < param_2) {
    if (uVar5 == 0xffffffff) {
      CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
    }
    uVar5 = uVar5 - 1;
    if (((*(int *)(iVar1 + 4 + uVar5 * 0x14) < param_3) &&
        (param_3 <= *(int *)(iVar1 + uVar5 * 0x14 + 8))) || (uVar4 = uVar2, uVar5 == 0xffffffff)) {
      param_2 = param_2 + -1;
      uVar4 = uVar5;
      uVar3 = uVar2;
    }
  }
  uVar5 = uVar5 + 1;
  *(uint *)param_4 = uVar5;
  *(uint *)param_5 = uVar3;
  if ((*(uint *)(param_1 + 0xc) < uVar3) || (uVar3 < uVar5)) {
    CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
  }
  return iVar1 + uVar5 * 0x14;
}
