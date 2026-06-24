/* address: 0x00444960 */
/* name: CDestroyableSegmentComponent__RemoveOwnerLinkAndResetBase */
/* signature: void __fastcall CDestroyableSegmentComponent__RemoveOwnerLinkAndResetBase(void * param_1) */


void __fastcall CDestroyableSegmentComponent__RemoveOwnerLinkAndResetBase(void *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d21c8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  if ((*(int *)((int)param_1 + 0x40) != 0) &&
     (this = *(void **)(*(int *)((int)param_1 + 0x40) + 4), ExceptionList = &local_c,
     this != (void *)0x0)) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)((int)param_1 + 0x40));
  }
  local_4 = 0xffffffff;
  CDestroyableSegment__ctor_like_00442660(param_1);
  ExceptionList = local_c;
  return;
}
