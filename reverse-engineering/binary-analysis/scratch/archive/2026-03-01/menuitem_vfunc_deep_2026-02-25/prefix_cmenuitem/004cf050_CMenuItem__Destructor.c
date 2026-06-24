/* address: 0x004cf050 */
/* name: CMenuItem__Destructor */
/* signature: undefined CMenuItem__Destructor(void) */


void __fastcall CMenuItem__Destructor(undefined4 *param_1)

{
  void *this;
  void *pvStack_c;
  undefined1 *puStack_8;
  uint uStack_4;

  puStack_8 = &LAB_005d36a3;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  *param_1 = &PTR_CMenuItem__ScalarDestructor_005dc520;
  uStack_4 = 1;
  if (param_1[7] != 0) {
    CUnit__Unk_004f27e0(param_1[7] + 8);
    param_1[7] = 0;
  }
  if (param_1[8] != 0) {
    CUnit__Unk_004f27e0(param_1[8] + 8);
    param_1[8] = 0;
  }
  uStack_4 = uStack_4 & 0xffffff00;
  if ((param_1[0xd] != 0) && (this = *(void **)(param_1[0xd] + 4), this != (void *)0x0)) {
    CSPtrSet__Remove(this,param_1 + 0xd);
  }
  *param_1 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
  ExceptionList = pvStack_c;
  return;
}
