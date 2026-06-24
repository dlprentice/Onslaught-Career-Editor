/* address: 0x0041ad10 */
/* name: CMCTentacle__AddVec3InPlace */
/* signature: void __thiscall CMCTentacle__AddVec3InPlace(void * this, void * param_1, void * param_2) */


void __thiscall CMCTentacle__AddVec3InPlace(void *this,void *param_1,void *param_2)

{
  *(float *)this = *(float *)param_1 + *(float *)this;
  *(float *)((int)this + 4) = *(float *)((int)param_1 + 4) + *(float *)((int)this + 4);
  *(float *)((int)this + 8) = *(float *)((int)param_1 + 8) + *(float *)((int)this + 8);
  return;
}
