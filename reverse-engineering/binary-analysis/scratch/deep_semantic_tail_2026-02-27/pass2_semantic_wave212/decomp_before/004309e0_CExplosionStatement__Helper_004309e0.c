/* address: 0x004309e0 */
/* name: CExplosionStatement__Helper_004309e0 */
/* signature: void __cdecl CExplosionStatement__Helper_004309e0(void * param_1) */


void __cdecl CExplosionStatement__Helper_004309e0(void *param_1)

{
  int iVar1;
  char cVar2;
  undefined4 *item;
  int iVar3;
  undefined4 uVar4;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d1dd9;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  item = (undefined4 *)OID__AllocObject(0x50,0x3f,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x96a)
  ;
  local_4 = 0;
  if (item == (undefined4 *)0x0) {
    item = (undefined4 *)0x0;
  }
  else {
    iVar3 = 0;
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar1 = iVar3 + 1;
      iVar3 = iVar3 + 1;
      cVar2 = *(char *)(iVar1 + (int)param_1);
    }
    uVar4 = OID__AllocObject(iVar3 + 1,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x4dc);
    item[0xc] = uVar4;
    iVar3 = 0;
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar3 = iVar3 + 1;
      *(char *)(item[0xc] + -1 + iVar3) = cVar2;
      cVar2 = *(char *)(iVar3 + (int)param_1);
    }
    *(undefined1 *)(item[0xc] + iVar3) = 0;
    *item = 0;
    item[1] = 0;
    item[2] = 0;
    item[3] = 0;
    item[0xd] = 0;
    item[0xe] = 0;
    item[0xf] = 1;
    item[0x10] = 10;
    item[4] = 0;
    item[5] = 0;
    item[0x11] = 0;
    item[0x13] = 0xffffffff;
    item[0x12] = 0;
    item[6] = 0;
    item[7] = 0;
    item[8] = 0;
    item[9] = 0;
    item[10] = 0;
    item[0xb] = 0;
  }
  local_4 = 0xffffffff;
  CSPtrSet__AddToTail(DAT_008553f8,item);
  ExceptionList = local_c;
  return;
}
