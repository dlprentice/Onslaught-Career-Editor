/* address: 0x004fd4d0 */
/* name: CCannon__Helper_004fd4d0 */
/* signature: void __thiscall CCannon__Helper_004fd4d0(void * this, void * param_1, int param_2) */


void __thiscall CCannon__Helper_004fd4d0(void *this,void *param_1,int param_2)

{
  void *unaff_retaddr;

  if (*(int *)((int)this + 0x178) != 0) {
    CDiveBomber__SelectTarget(param_1);
    return;
  }
  CThing__Unk_004f3ac0(this,(int)param_1,unaff_retaddr);
  return;
}
