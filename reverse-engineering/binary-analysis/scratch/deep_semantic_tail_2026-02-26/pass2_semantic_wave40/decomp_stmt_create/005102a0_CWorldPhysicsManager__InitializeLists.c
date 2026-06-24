/* address: 0x005102a0 */
/* name: CWorldPhysicsManager__InitializeLists */
/* signature: undefined CWorldPhysicsManager__InitializeLists(void) */


void CWorldPhysicsManager__InitializeLists(void)

{
  void *pvVar1;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d65b1;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x12d);
  local_4 = 0;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553e8 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x12e);
  local_4 = 1;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553ec = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x12f);
  local_4 = 2;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553f0 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x130);
  local_4 = 3;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553f4 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x131);
  local_4 = 4;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553f8 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x132);
  local_4 = 5;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_008553fc = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x133);
  local_4 = 6;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_00855400 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x134);
  local_4 = 7;
  if (pvVar1 == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar1);
  }
  local_4 = 0xffffffff;
  DAT_00855404 = pvVar1;
  pvVar1 = (void *)OID__AllocObject(0x10,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x135);
  local_4 = 8;
  if (pvVar1 != (void *)0x0) {
    CSPtrSet__Init(pvVar1);
    DAT_00855408 = pvVar1;
    ExceptionList = local_c;
    return;
  }
  DAT_00855408 = (void *)0x0;
  ExceptionList = local_c;
  return;
}
