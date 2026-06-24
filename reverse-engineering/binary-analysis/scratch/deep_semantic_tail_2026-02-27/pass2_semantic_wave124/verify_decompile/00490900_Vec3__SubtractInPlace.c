/* address: 0x00490900 */
/* name: Vec3__SubtractInPlace */
/* signature: void __thiscall Vec3__SubtractInPlace(void * this, void * param_1, void * param_2) */


void __thiscall Vec3__SubtractInPlace(void *this,void *param_1,void *param_2)

{
  *(float *)this = *(float *)this - *(float *)param_1;
  *(float *)((int)this + 4) = *(float *)((int)this + 4) - *(float *)((int)param_1 + 4);
  *(float *)((int)this + 8) = *(float *)((int)this + 8) - *(float *)((int)param_1 + 8);
  return;
}
