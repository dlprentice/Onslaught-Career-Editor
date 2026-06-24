/* address: 0x00431350 */
/* name: CUnitAI__Unk_00431350 */
/* signature: void __cdecl CUnitAI__Unk_00431350(void * param_1) */


void __cdecl CUnitAI__Unk_00431350(void *param_1)

{
  char cVar1;
  undefined4 *item;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  char *pcVar5;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d1e99;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  item = (undefined4 *)OID__AllocObject(0x24,0x41,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x97f)
  ;
  local_4 = 0;
  if (item == (undefined4 *)0x0) {
    item = (undefined4 *)0x0;
  }
  else {
    uVar3 = 0xffffffff;
    pcVar2 = param_1;
    do {
      if (uVar3 == 0) break;
      uVar3 = uVar3 - 1;
      cVar1 = *pcVar2;
      pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    pcVar2 = (char *)OID__AllocObject(~uVar3,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x109);
    uVar3 = 0xffffffff;
    item[8] = pcVar2;
    do {
      pcVar5 = param_1;
      if (uVar3 == 0) break;
      uVar3 = uVar3 - 1;
      pcVar5 = (char *)((int)param_1 + 1);
      cVar1 = *(char *)param_1;
      param_1 = pcVar5;
    } while (cVar1 != '\0');
    uVar3 = ~uVar3;
    pcVar5 = pcVar5 + -uVar3;
    for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *(undefined4 *)pcVar2 = *(undefined4 *)pcVar5;
      pcVar5 = pcVar5 + 4;
      pcVar2 = pcVar2 + 4;
    }
    for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *pcVar2 = *pcVar5;
      pcVar5 = pcVar5 + 1;
      pcVar2 = pcVar2 + 1;
    }
    item[6] = 0;
    item[4] = 0;
    item[5] = 0;
    *item = 0;
    item[2] = 0xffffffff;
    item[1] = 0;
    item[3] = 0;
    item[7] = 0xffffffff;
  }
  local_4 = 0xffffffff;
  CSPtrSet__AddToTail(DAT_00855404,item);
  ExceptionList = local_c;
  return;
}
