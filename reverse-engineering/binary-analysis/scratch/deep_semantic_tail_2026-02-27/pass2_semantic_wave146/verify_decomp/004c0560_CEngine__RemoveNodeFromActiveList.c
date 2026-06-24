/* address: 0x004c0560 */
/* name: CEngine__RemoveNodeFromActiveList */
/* signature: void __thiscall CEngine__RemoveNodeFromActiveList(void * this, int param_1, void * param_2) */


void __thiscall CEngine__RemoveNodeFromActiveList(void *this,int param_1,void *param_2)

{
  int unaff_retaddr;

  if (*(int *)((int)this + 0x58) == param_1) {
    *(undefined4 *)((int)this + 0x58) = 0;
  }
  if (*(int *)param_1 == 0) {
    *(undefined4 *)((int)this + 0x54) = *(undefined4 *)(param_1 + 4);
  }
  else {
    *(undefined4 *)(*(int *)param_1 + 4) = *(undefined4 *)(param_1 + 4);
  }
  if (*(undefined4 **)(param_1 + 4) == (undefined4 *)0x0) {
    *(undefined4 *)((int)this + 0x50) = *(undefined4 *)param_1;
  }
  else {
    **(undefined4 **)(param_1 + 4) = *(undefined4 *)param_1;
  }
  *(undefined4 *)param_1 = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  if (*(int *)((int)this + 0x54) == 0) {
    CEngine__UnlinkNodeFromDoublyLinkedList(&DAT_0082b400,(int)this,unaff_retaddr);
  }
  return;
}
