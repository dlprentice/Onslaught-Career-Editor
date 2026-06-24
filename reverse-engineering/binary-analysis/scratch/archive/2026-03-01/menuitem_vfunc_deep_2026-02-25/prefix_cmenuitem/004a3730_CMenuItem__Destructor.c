/* address: 0x004a3730 */
/* name: CMenuItem__Destructor */
/* signature: undefined CMenuItem__Destructor(void) */


void __fastcall CMenuItem__Destructor(undefined4 *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  puStack_8 = &LAB_005d36a3;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *param_1 = &PTR_CMenuItem__ScalarDestructor_005dc520;
  local_4 = 1;
  if (param_1[7] != 0) {
    CUnit__Unk_004f27e0(param_1[7] + 8);
    param_1[7] = 0;
  }
  if (param_1[8] != 0) {
    CUnit__Unk_004f27e0(param_1[8] + 8);
    param_1[8] = 0;
  }
  local_4 = local_4 & 0xffffff00;
  if ((param_1[0xd] != 0) && (this = *(void **)(param_1[0xd] + 4), this != (void *)0x0)) {
    CSPtrSet__Remove(this,param_1 + 0xd);
  }
  *param_1 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
  ExceptionList = local_c;
  return;
}
