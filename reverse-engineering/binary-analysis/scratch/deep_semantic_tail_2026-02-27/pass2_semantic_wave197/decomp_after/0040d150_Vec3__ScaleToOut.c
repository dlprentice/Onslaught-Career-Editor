/* address: 0x0040d150 */
/* name: Vec3__ScaleToOut */
/* signature: void __thiscall Vec3__ScaleToOut(void * this, void * param_1, void * param_2, float param_3) */


void __thiscall Vec3__ScaleToOut(void *this,void *param_1,void *param_2,float param_3)

{
  float fVar1;
  float fVar2;

  fVar1 = *(float *)((int)this + 8);
  fVar2 = *(float *)((int)this + 4);
  *(float *)param_1 = (float)param_2 * *(float *)this;
  *(float *)((int)param_1 + 4) = (float)param_2 * fVar2;
  *(float *)((int)param_1 + 8) = (float)param_2 * fVar1;
  return;
}
