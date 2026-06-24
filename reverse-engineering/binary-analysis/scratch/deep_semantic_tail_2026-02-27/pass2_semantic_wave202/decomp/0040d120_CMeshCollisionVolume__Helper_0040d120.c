/* address: 0x0040d120 */
/* name: CMeshCollisionVolume__Helper_0040d120 */
/* signature: void __thiscall CMeshCollisionVolume__Helper_0040d120(void * this, void * param_1, void * param_2, void * param_3) */


void __thiscall
CMeshCollisionVolume__Helper_0040d120(void *this,void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;

  fVar1 = *(float *)((int)this + 8);
  fVar2 = *(float *)((int)param_2 + 8);
  fVar3 = *(float *)((int)this + 4);
  fVar4 = *(float *)((int)param_2 + 4);
  *(float *)param_1 = *(float *)this - *(float *)param_2;
  *(float *)((int)param_1 + 4) = fVar3 - fVar4;
  *(float *)((int)param_1 + 8) = fVar1 - fVar2;
  return;
}
