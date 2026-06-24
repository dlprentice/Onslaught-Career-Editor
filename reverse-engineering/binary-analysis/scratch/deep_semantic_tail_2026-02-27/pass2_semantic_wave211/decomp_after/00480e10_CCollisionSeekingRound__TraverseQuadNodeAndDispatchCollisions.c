/* address: 0x00480e10 */
/* name: CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions */
/* signature: void __thiscall CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(void * this, int param_1, void * param_2) */


void __thiscall
CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(void *this,int param_1,void *param_2)

{
  int extraout_EAX;
  int iVar1;
  int *piVar2;
  void *unaff_EDI;

  piVar2 = *(int **)param_1;
  if (piVar2 != (int *)0x0) {
    CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(this,*piVar2,unaff_EDI);
    CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(this,piVar2[1],unaff_EDI);
    CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(this,piVar2[2],unaff_EDI);
    CCollisionSeekingRound__TraverseQuadNodeAndDispatchCollisions(this,piVar2[3],unaff_EDI);
  }
  CCollisionSeekingRound__IterSetHeadFromMapWhoEntry(&DAT_00704200,(void *)param_1,(int)unaff_EDI);
  iVar1 = extraout_EAX;
  while (iVar1 != 0) {
    iVar1 = CMapWhoEntry__GetOwner();
    piVar2 = (int *)CCollisionSeekingRound__GetCollisionComponentOrNull(iVar1);
    if ((((piVar2 != (int *)0x0) && (piVar2 != *(int **)((int)this + 8))) &&
        (iVar1 = (**(code **)(**(int **)((int)this + 8) + 0x20))(piVar2), iVar1 != 0)) &&
       (iVar1 = (**(code **)(*piVar2 + 0x20))(*(undefined4 *)((int)this + 8)), iVar1 != 0)) {
      if (*(int *)((int)this + 0x10) == 1) {
        CConsole__Printf(&DAT_0066f580,s_WARNING__Unexpected_collision_ch_0062cdec);
      }
      else {
        CHLCollisionDetector__DispatchCollisionEventForPair(this,piVar2,unaff_EDI);
        *(undefined4 *)((int)this + 0x10) = 0;
      }
    }
    iVar1 = CCollisionSeekingRound__IterPopNextEntry(&DAT_00704200);
  }
  return;
}
