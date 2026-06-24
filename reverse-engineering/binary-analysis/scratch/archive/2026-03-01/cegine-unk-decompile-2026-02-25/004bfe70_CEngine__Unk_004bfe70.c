/* address: 0x004bfe70 */
/* name: CEngine__Unk_004bfe70 */
/* signature: void __fastcall CEngine__Unk_004bfe70(int param_1) */


void __fastcall CEngine__Unk_004bfe70(int param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d3fa8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  if ((*(int *)(param_1 + 0x3c) != 0) &&
     (this = *(void **)(*(int *)(param_1 + 0x3c) + 4), ExceptionList = &local_c, this != (void *)0x0
     )) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)(param_1 + 0x3c));
  }
  local_4 = 0xffffffff;
  CThing__ctor_like_004f3640((void *)param_1);
  ExceptionList = local_c;
  return;
}
