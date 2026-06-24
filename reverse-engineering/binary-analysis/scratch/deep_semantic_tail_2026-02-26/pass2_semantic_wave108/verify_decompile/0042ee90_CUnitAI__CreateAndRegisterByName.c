/* address: 0x0042ee90 */
/* name: CUnitAI__CreateAndRegisterByName */
/* signature: void __cdecl CUnitAI__CreateAndRegisterByName(void * param_1) */


void __cdecl CUnitAI__CreateAndRegisterByName(void *param_1)

{
  int iVar1;
  char cVar2;
  void *item;
  int iVar3;
  undefined4 uVar4;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d1c45;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  item = (void *)OID__AllocObject(0x1ac,0xf,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x971);
  local_4 = 0;
  if (item == (void *)0x0) {
    item = (void *)0x0;
  }
  else {
    CSPtrSet__Init((void *)((int)item + 0x3c));
    local_4._0_1_ = 1;
    CSPtrSet__Init((void *)((int)item + 0x4c));
    local_4._0_1_ = 2;
    CSPtrSet__Init((void *)((int)item + 0x5c));
    local_4._0_1_ = 3;
    CSPtrSet__Init((void *)((int)item + 0x6c));
    iVar3 = 0;
    local_4 = CONCAT31(local_4._1_3_,4);
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar1 = iVar3 + 1;
      iVar3 = iVar3 + 1;
      cVar2 = *(char *)(iVar1 + (int)param_1);
    }
    uVar4 = OID__AllocObject(iVar3 + 1,0xf,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x657);
    *(undefined4 *)((int)item + 0xb0) = uVar4;
    iVar3 = 0;
    cVar2 = *(char *)param_1;
    while (cVar2 != '\0') {
      iVar3 = iVar3 + 1;
      *(char *)(*(int *)((int)item + 0xb0) + -1 + iVar3) = cVar2;
      cVar2 = *(char *)(iVar3 + (int)param_1);
    }
    *(undefined1 *)(*(int *)((int)item + 0xb0) + iVar3) = 0;
    CUnitAI__InitDefaults(item);
    iVar3 = stricmp(s_Fenrir_Main_Gun_00624890,param_1);
    if ((iVar3 == 0) || (iVar3 = stricmp(s_Fenrir_00625848,param_1), iVar3 == 0)) {
      *(undefined4 *)((int)item + 0x1a4) = 1;
    }
  }
  local_4 = 0xffffffff;
  CSPtrSet__AddToTail(DAT_008553fc,item);
  ExceptionList = local_c;
  return;
}
