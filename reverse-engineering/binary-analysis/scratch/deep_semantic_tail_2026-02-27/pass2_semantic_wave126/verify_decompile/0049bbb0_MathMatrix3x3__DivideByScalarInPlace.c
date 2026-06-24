/* address: 0x0049bbb0 */
/* name: MathMatrix3x3__DivideByScalarInPlace */
/* signature: void __thiscall MathMatrix3x3__DivideByScalarInPlace(void * this, void * param_1, float param_2) */


void __thiscall MathMatrix3x3__DivideByScalarInPlace(void *this,void *param_1,float param_2)

{
  *(float *)this = *(float *)this / (float)param_1;
  *(float *)((int)this + 4) = *(float *)((int)this + 4) / (float)param_1;
  *(float *)((int)this + 8) = *(float *)((int)this + 8) / (float)param_1;
  *(float *)((int)this + 0x10) = *(float *)((int)this + 0x10) / (float)param_1;
  *(float *)((int)this + 0x14) = *(float *)((int)this + 0x14) / (float)param_1;
  *(float *)((int)this + 0x18) = *(float *)((int)this + 0x18) / (float)param_1;
  *(float *)((int)this + 0x20) = *(float *)((int)this + 0x20) / (float)param_1;
  *(float *)((int)this + 0x24) = *(float *)((int)this + 0x24) / (float)param_1;
  *(float *)((int)this + 0x28) = *(float *)((int)this + 0x28) / (float)param_1;
  return;
}
