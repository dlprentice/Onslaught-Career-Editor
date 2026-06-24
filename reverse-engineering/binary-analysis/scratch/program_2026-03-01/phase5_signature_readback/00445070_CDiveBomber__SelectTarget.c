/* address: 0x00445070 */
/* name: CDiveBomber__SelectTarget */
/* signature: void * __thiscall CDiveBomber__SelectTarget(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void * __thiscall CDiveBomber__SelectTarget(void *this)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  void *pvVar5;
  void *extraout_EAX;
  int iVar6;
  void *unaff_ESI;
  int in_stack_00000004;
  int iStack_3c;
  int iStack_38;

  iVar3 = (**(code **)(**(int **)(*(int *)((int)this + 0x10) + 0x30) + 0x24))();
  iVar6 = 0;
  iStack_3c = 0;
  iStack_38 = 0;
  if (0 < *(int *)(iVar3 + 0x15c)) {
    do {
      iVar1 = *(int *)(*(int *)(iVar3 + 0x160) + iVar6 * 4);
      if ((((iVar1 != 0) &&
           (piVar2 = *(int **)(*(int *)((int)this + 4) + *(int *)(iVar1 + 0x88) * 4),
           piVar2 != (int *)0x0)) && (iVar4 = (**(code **)(*piVar2 + 0x14))(), iVar4 == 0)) &&
         ((_DAT_005d856c < (float)piVar2[3] && (iStack_3c < piVar2[0x10])))) {
        iStack_3c = piVar2[0x10];
        iStack_38 = iVar1;
      }
      iVar6 = iVar6 + 1;
    } while (iVar6 < *(int *)(iVar3 + 0x15c));
    if (iStack_38 != 0) {
      pvVar5 = (void *)CMeshPart__EvaluatePoseTransformForFrame();
      return pvVar5;
    }
  }
  CUnitAI__GetWorldPositionForTargeting(*(void **)((int)this + 0x10),in_stack_00000004,unaff_ESI);
  return extraout_EAX;
}
