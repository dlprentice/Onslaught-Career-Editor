/* address: 0x004812d0 */
/* name: CHLCollisionDetector__VFunc_00_004812d0 */
/* signature: void __thiscall CHLCollisionDetector__VFunc_00_004812d0(void * this, void * param_1, int param_2) */


void __thiscall CHLCollisionDetector__VFunc_00_004812d0(void *this,void *param_1,int param_2)

{
  int iVar1;
  void *unaff_ESI;

  if ((*(short *)((int)param_1 + 4) == 2000) && (iVar1 = *(int *)((int)param_1 + 0xc), iVar1 != 0))
  {
    *(void **)((int)this + 0xc) = param_1;
    CUnitAI__Unk_00480c90(this,iVar1,unaff_ESI);
    *(undefined4 *)((int)this + 0x10) = 0;
    *(undefined4 *)((int)this + 0xc) = 0;
  }
  return;
}
