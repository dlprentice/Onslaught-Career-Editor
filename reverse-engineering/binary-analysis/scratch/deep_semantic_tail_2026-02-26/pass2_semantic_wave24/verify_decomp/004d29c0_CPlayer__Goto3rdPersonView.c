/* address: 0x004d29c0 */
/* name: CPlayer__Goto3rdPersonView */
/* signature: undefined CPlayer__Goto3rdPersonView(void) */


void __fastcall CPlayer__Goto3rdPersonView(int param_1)

{
  void *pvVar1;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d4796;
  local_c = ExceptionList;
  if (*(int *)(param_1 + 0x1c) != 0) {
    ExceptionList = &local_c;
    *(undefined4 *)(param_1 + 0x24) = 2;
    pvVar1 = (void *)OID__AllocObject(0xc,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0x43);
    local_4 = 0;
    if (pvVar1 == (void *)0x0) {
      pvVar1 = (void *)0x0;
    }
    else {
      pvVar1 = CThing3rdPersonCamera__ctor(pvVar1,*(void **)(param_1 + 0x1c));
    }
    local_4 = 0xffffffff;
    CGame__SetCurrentCamera(&DAT_008a9a98,*(int *)(param_1 + 0x2c) + -1,pvVar1,'\x01');
  }
  ExceptionList = local_c;
  return;
}
