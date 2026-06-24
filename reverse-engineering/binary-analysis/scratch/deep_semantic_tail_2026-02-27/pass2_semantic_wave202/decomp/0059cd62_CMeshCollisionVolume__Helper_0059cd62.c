/* address: 0x0059cd62 */
/* name: CMeshCollisionVolume__Helper_0059cd62 */
/* signature: bool __stdcall CMeshCollisionVolume__Helper_0059cd62(void * param_1) */


bool CMeshCollisionVolume__Helper_0059cd62(void *param_1)

{
  void *pvVar1;
  int iVar2;
  bool bVar3;

  pvVar1 = param_1;
  bVar3 = true;
  if ((*(byte *)((int)param_1 + 0x10c) & 0x20) == 0) {
    if ((*(byte *)((int)param_1 + 0x5d) & 8) == 0) goto LAB_0059cd8e;
  }
  else if ((*(uint *)((int)param_1 + 0x5c) & 0x300) != 0x300) goto LAB_0059cd8e;
  bVar3 = false;
LAB_0059cd8e:
  CDXTexture__ReadFromSource(param_1,(int)&param_1,4);
  if (bVar3) {
    iVar2 = CDXTexture__ReadU32BigEndian(&param_1);
    bVar3 = iVar2 != *(int *)((int)pvVar1 + 0x100);
  }
  else {
    bVar3 = false;
  }
  return bVar3;
}
