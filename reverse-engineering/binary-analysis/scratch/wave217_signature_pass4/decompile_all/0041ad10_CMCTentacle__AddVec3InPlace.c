/* address: 0x0041ad10 */
/* name: CMCTentacle__AddVec3InPlace */
/* signature: void __thiscall CMCTentacle__AddVec3InPlace(void * this, void * lhs_vec3, void * rhs_vec3) */


void __thiscall CMCTentacle__AddVec3InPlace(void *this,void *lhs_vec3,void *rhs_vec3)

{
  *(float *)this = *(float *)lhs_vec3 + *(float *)this;
  *(float *)((int)this + 4) = *(float *)((int)lhs_vec3 + 4) + *(float *)((int)this + 4);
  *(float *)((int)this + 8) = *(float *)((int)lhs_vec3 + 8) + *(float *)((int)this + 8);
  return;
}
