/* address: 0x004f9a60 */
/* name: CDestroyableSegment__RemoveLinkedSegmentAndRelease */
/* signature: void __thiscall CDestroyableSegment__RemoveLinkedSegmentAndRelease(void * this, int param_1, void * param_2) */


void __thiscall
CDestroyableSegment__RemoveLinkedSegmentAndRelease(void *this,int param_1,void *param_2)

{
  if (param_1 != 0) {
    CSPtrSet__Remove((void *)((int)this + 0x18c),(void *)param_1);
    (**(code **)(*(int *)param_1 + 4))(1);
  }
  return;
}
