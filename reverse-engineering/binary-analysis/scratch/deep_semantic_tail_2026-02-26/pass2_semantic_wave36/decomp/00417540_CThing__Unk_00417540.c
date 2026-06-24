/* address: 0x00417540 */
/* name: CThing__Unk_00417540 */
/* signature: void __thiscall CThing__Unk_00417540(void * this, void * param_1, int param_2) */


void __thiscall CThing__Unk_00417540(void *this,void *param_1,int param_2)

{
  uint unaff_ESI;

  if ((*(int *)((int)this + 0x178) != 0) || ((*(byte *)((int)this + 0x2c) & 4) == 0)) {
    CThing__Unk_004f36d0(this,(int)param_1,unaff_ESI);
    CStaticShadows__UpdateVisibility(this,0);
    if ((0 < DAT_00660540) && (DAT_00660540 = DAT_00660540 + -1, 0 < DAT_00660540)) {
      (**(code **)(*(int *)this + 0xd0))();
    }
  }
  return;
}
