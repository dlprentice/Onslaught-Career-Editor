/* address: 0x004b6cd0 */
/* name: COggLoader__InitReadAndWaitThread */
/* signature: void __thiscall COggLoader__InitReadAndWaitThread(void * this) */


void __thiscall COggLoader__InitReadAndWaitThread(void *this)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d3afb;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  COggFileRead__ctor_like_00524600((void *)(-(uint)(this != (void *)0x20) & (uint)this));
  local_4 = 0xffffffff;
  CWaitingThread__ctor_like_00528bf0();
  ExceptionList = local_c;
  return;
}
