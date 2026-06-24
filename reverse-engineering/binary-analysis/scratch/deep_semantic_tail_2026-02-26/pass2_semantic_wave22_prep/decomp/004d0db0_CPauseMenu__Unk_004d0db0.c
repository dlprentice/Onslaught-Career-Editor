/* address: 0x004d0db0 */
/* name: CPauseMenu__Unk_004d0db0 */
/* signature: void * __thiscall CPauseMenu__Unk_004d0db0(void * this, void * param_1, int param_2, int param_3, void * param_4) */


void * __thiscall
CPauseMenu__Unk_004d0db0(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  void *unaff_ESI;

  CPauseMenu__Helper_0044ae20(this,(void *)param_3,param_2,unaff_ESI);
  *(void **)((int)this + 8) = param_1;
  return this;
}
