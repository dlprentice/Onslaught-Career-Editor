/* address: 0x004b7ca0 */
/* name: IScript__Helper_004b7ca0 */
/* signature: void __thiscall IScript__Helper_004b7ca0(void * this, int param_1, void * param_2) */


void __thiscall IScript__Helper_004b7ca0(void *this,int param_1,void *param_2)

{
  int *piVar1;
  bool bVar2;
  void *item;
  undefined1 local_1c [16];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d3bb8;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CSPtrSet__Init(local_1c);
  piVar1 = *(int **)((int)this + 0xc);
  bVar2 = false;
  local_4 = 0;
  *(int **)((int)this + 0x14) = piVar1;
  if (piVar1 == (int *)0x0) {
    item = (void *)0x0;
  }
  else {
    item = (void *)*piVar1;
  }
  if (item != (void *)0x0) {
    do {
      if ((*(int *)(param_1 + 0x2c) < *(int *)((int)item + 0x2c)) && (!bVar2)) {
        CSPtrSet__AddToTail(local_1c,(void *)param_1);
        bVar2 = true;
      }
      CSPtrSet__AddToTail(local_1c,item);
      piVar1 = *(int **)(*(int *)((int)this + 0x14) + 4);
      *(int **)((int)this + 0x14) = piVar1;
      if (piVar1 == (int *)0x0) {
        item = (void *)0x0;
      }
      else {
        item = (void *)*piVar1;
      }
    } while (item != (void *)0x0);
    if (bVar2) goto LAB_004b7d3c;
  }
  CSPtrSet__AddToTail(local_1c,(void *)param_1);
LAB_004b7d3c:
  CSPtrSet__operator_assign((void *)((int)this + 0xc),local_1c);
  if ((*(int *)((int)this + 0x18) == 1) && (*(int *)((int)this + 0x30) == 1)) {
    CDropship__TryAdvanceQueuedPortrait(this);
  }
  local_4 = 0xffffffff;
  CSPtrSet__Clear(local_1c);
  ExceptionList = local_c;
  return;
}
