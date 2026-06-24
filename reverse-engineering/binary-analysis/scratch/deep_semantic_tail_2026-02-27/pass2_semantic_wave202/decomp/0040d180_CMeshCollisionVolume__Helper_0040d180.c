/* address: 0x0040d180 */
/* name: CMeshCollisionVolume__Helper_0040d180 */
/* signature: double __thiscall CMeshCollisionVolume__Helper_0040d180(void * this, void * param_1, void * param_2) */


double __thiscall CMeshCollisionVolume__Helper_0040d180(void *this,void *param_1,void *param_2)

{
  return (double)(*(float *)param_1 * *(float *)this +
                 *(float *)((int)param_1 + 4) * *(float *)((int)this + 4) +
                 *(float *)((int)param_1 + 8) * *(float *)((int)this + 8));
}
