/* address: 0x0042fa80 */
/* name: CWeaponModeStatement__Create */
/* signature: void __cdecl CWeaponModeStatement__Create(void * param_1) */


void __cdecl CWeaponModeStatement__Create(void *param_1)

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
  puStack_8 = &LAB_005d1cef;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  item = (undefined4 *)OID__AllocObject(0xc0,0x3c,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x955)
  ;
  local_4 = 0;
  if (item == (undefined4 *)0x0) {
    item = (undefined4 *)0x0;
  }
  else {
    CSPtrSet__Init(item + 0x13);
    local_4._0_1_ = 1;
    CSPtrSet__Init(item + 0x17);
    iVar3 = 0;
    local_4 = CONCAT31(local_4._1_3_,2);
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar1 = iVar3 + 1;
      iVar3 = iVar3 + 1;
      cVar2 = *(char *)(iVar1 + (int)param_1);
    }
    uVar4 = OID__AllocObject(iVar3 + 1,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x2dc);
    item[0xc] = uVar4;
    iVar3 = 0;
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar3 = iVar3 + 1;
      *(char *)(item[0xc] + -1 + iVar3) = cVar2;
      cVar2 = *(char *)(iVar3 + (int)param_1);
    }
    *(undefined1 *)(item[0xc] + iVar3) = 0;
    item[0xd] = 0;
    item[0xe] = 0;
    item[0x11] = 1;
    item[0x12] = 1;
    item[0xf] = 0;
    item[6] = 0;
    item[1] = 0;
    item[2] = 0;
    *item = 0;
    item[3] = 0;
    item[4] = 0;
    item[5] = 0;
    item[0x1d] = 0;
    item[0x1e] = 0x42c80000;
    item[0x1b] = 0xc1200000;
    item[0x1c] = 0x461c4000;
    item[0x1f] = 0;
    item[0x20] = 0;
    item[0x21] = 0x3f000000;
    item[0x10] = 0;
    item[0x24] = 5;
    item[0x22] = 0;
    item[0x23] = 0;
    item[0x25] = 0;
    item[0x26] = 0;
    item[0x29] = 0;
    item[0x2a] = 0;
    item[0x27] = 0x42200000;
    item[0x28] = 0x41200000;
    item[0x2b] = 0;
    item[0x2c] = 0;
    item[0x2d] = 1;
    item[0x2e] = 0xffffffff;
    item[0x2f] = 0;
    item[7] = 0;
    item[8] = 0;
    item[9] = 0;
    item[10] = 0;
    item[0xb] = 0;
  }
  local_4 = 0xffffffff;
  CSPtrSet__AddToTail(DAT_008553ec,item);
  ExceptionList = local_c;
  return;
}
