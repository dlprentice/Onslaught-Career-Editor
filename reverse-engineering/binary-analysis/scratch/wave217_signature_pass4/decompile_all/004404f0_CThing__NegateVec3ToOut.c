/* address: 0x004404f0 */
/* name: CThing__NegateVec3ToOut */
/* signature: void __thiscall CThing__NegateVec3ToOut(void * this, void * src_vec3, void * out_vec3) */


void __thiscall CThing__NegateVec3ToOut(void *this,void *src_vec3,void *out_vec3)

{
  float fVar1;
  float fVar2;

  fVar1 = *(float *)((int)this + 8);
  fVar2 = *(float *)((int)this + 4);
  *(float *)src_vec3 = -*(float *)this;
  *(float *)((int)src_vec3 + 4) = -fVar2;
  *(float *)((int)src_vec3 + 8) = -fVar1;
  return;
}
