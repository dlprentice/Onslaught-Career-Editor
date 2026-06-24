/* address: 0x0059d614 */
/* name: CDXTexture__FinalizePngChunkAndVerifyCrc */
/* signature: int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * param_1, uint param_2) */


int CDXTexture__FinalizePngChunkAndVerifyCrc(void *param_1,uint param_2)

{
  uint uVar1;
  bool bVar2;
  byte bVar3;
  undefined3 extraout_var;
  int iVar4;

  uVar1 = *(uint *)((int)param_1 + 0xa0);
  for (; uVar1 < param_2; param_2 = param_2 - uVar1) {
    CTexture__Helper_0059cd4b(param_1,*(int *)((int)param_1 + 0x9c),*(int *)((int)param_1 + 0xa0));
  }
  if (param_2 != 0) {
    CTexture__Helper_0059cd4b(param_1,*(int *)((int)param_1 + 0x9c),param_2);
  }
  bVar2 = CMeshCollisionVolume__Helper_0059cd62(param_1);
  if (CONCAT31(extraout_var,bVar2) == 0) {
    iVar4 = 0;
  }
  else {
    bVar3 = *(byte *)((int)param_1 + 0x10c) & 0x20;
    if (((bVar3 == 0) || ((*(byte *)((int)param_1 + 0x5d) & 2) != 0)) &&
       ((bVar3 != 0 || ((*(byte *)((int)param_1 + 0x5d) & 4) == 0)))) {
      CDXTexture__LogChunkTagDiagnostic(param_1,0x5f3a6c);
    }
    else {
      CMeshCollisionVolume__Helper_00592d9e((int)param_1,0x5f3a6c);
    }
    iVar4 = 1;
  }
  return iVar4;
}
