/* address: 0x004a3450 */
/* name: CMenuItem__Clone */
/* signature: undefined CMenuItem__Clone(void) */


undefined4 * __fastcall CMenuItem__Clone(int param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d361f;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  puVar2 = (undefined4 *)OID__AllocObject(0x38,0x80,s_C__dev_ONSLAUGHT2_MenuItem_cpp_0062f7d8,0xad);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
    puVar2[2] = *(undefined4 *)(param_1 + 8);
    puVar2[4] = *(undefined4 *)(param_1 + 0x10);
    puVar2[5] = *(undefined4 *)(param_1 + 0x14);
    puVar2[3] = *(undefined4 *)(param_1 + 0xc);
    puVar2[0xd] = 0;
    *puVar2 = &PTR_CMenuItem__ScalarDestructor_005dc520;
    local_4 = 2;
    CGenericActiveReader__SetReader(puVar2 + 0xd,*(void **)(param_1 + 0x34));
    uVar1 = *(undefined4 *)(param_1 + 0x24);
    puVar2[7] = 0;
    puVar2[9] = uVar1;
    puVar2[8] = 0;
    ExceptionList = local_c;
    return puVar2;
  }
  ExceptionList = local_c;
  return (undefined4 *)0x0;
}
