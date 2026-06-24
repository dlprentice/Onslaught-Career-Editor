/* address: 0x004539d0 */
/* name: CControllerDefinition__dtor */
/* signature: void __thiscall CControllerDefinition__dtor(void * this) */


void __thiscall CControllerDefinition__dtor(void *this)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d2618;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined ***)this = &PTR_CControllerDefinition__scalar_deleting_dtor_005db404;
  local_4 = 0;
  if (g_ControlRemapActive == '\0') {
    g_ControlRemapActive = '\x01';
    PLATFORM__SetKeySink((void *)0x0);
  }
  if (*(int *)((int)this + 0x2c) != 0) {
    CUnit__Unk_004f27e0(*(int *)((int)this + 0x2c) + 8);
    *(undefined4 *)((int)this + 0x2c) = 0;
  }
  *(undefined ***)this = &PTR_LAB_005db440;
  ExceptionList = local_c;
  return;
}
