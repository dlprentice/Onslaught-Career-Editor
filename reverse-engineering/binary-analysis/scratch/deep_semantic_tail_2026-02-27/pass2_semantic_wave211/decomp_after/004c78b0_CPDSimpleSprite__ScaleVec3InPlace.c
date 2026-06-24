/* address: 0x004c78b0 */
/* name: CPDSimpleSprite__ScaleVec3InPlace */
/* signature: void __thiscall CPDSimpleSprite__ScaleVec3InPlace(void * this, void * param_1, float param_2) */


void __thiscall CPDSimpleSprite__ScaleVec3InPlace(void *this,void *param_1,float param_2)

{
  *(float *)this = (float)param_1 * *(float *)this;
  *(float *)((int)this + 4) = (float)param_1 * *(float *)((int)this + 4);
  *(float *)((int)this + 8) = (float)param_1 * *(float *)((int)this + 8);
  return;
}
