/* address: 0x004539d0 */
/* name: CControllerDefinition__ctor_like_004539d0 */
/* signature: void __fastcall CControllerDefinition__ctor_like_004539d0(void * param_1) */


void __fastcall CControllerDefinition__ctor_like_004539d0(void *param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d2618;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined ***)param_1 = &PTR_CControllerDefinition__VFunc_00_004539b0_005db404;
  local_4 = 0;
  if (g_ControlRemapActive == '\0') {
    g_ControlRemapActive = '\x01';
    PLATFORM__SetKeySink((void *)0x0);
  }
  if (*(int *)((int)param_1 + 0x2c) != 0) {
    CUnit__Unk_004f27e0(*(int *)((int)param_1 + 0x2c) + 8);
    *(undefined4 *)((int)param_1 + 0x2c) = 0;
  }
  *(undefined ***)param_1 = &PTR_LAB_005db440;
  ExceptionList = local_c;
  return;
}
