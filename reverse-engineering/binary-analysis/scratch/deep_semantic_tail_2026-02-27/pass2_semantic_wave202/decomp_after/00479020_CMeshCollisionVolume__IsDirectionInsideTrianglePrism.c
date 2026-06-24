/* address: 0x00479020 */
/* name: CMeshCollisionVolume__IsDirectionInsideTrianglePrism */
/* signature: int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl
CMeshCollisionVolume__IsDirectionInsideTrianglePrism
          (void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  void *unaff_EDI;
  double dVar5;
  float local_40;
  float local_3c;
  float local_38;
  float local_30;
  float local_2c;
  float local_28;
  undefined1 local_20 [16];
  undefined1 local_10 [16];

  fVar3 = *(float *)((int)param_2 + 4) - *(float *)((int)param_1 + 4);
  fVar2 = *(float *)((int)param_2 + 8) - *(float *)((int)param_1 + 8);
  local_40 = *(float *)param_3 - *(float *)param_2;
  fVar1 = *(float *)((int)param_3 + 4) - *(float *)((int)param_2 + 4);
  fVar4 = *(float *)((int)param_3 + 8) - *(float *)((int)param_2 + 8);
  local_30 = fVar4 * fVar3 - fVar1 * fVar2;
  if (local_30 * *(float *)param_5 +
      (fVar1 * (*(float *)param_2 - *(float *)param_1) - local_40 * fVar3) *
      *(float *)((int)param_5 + 8) +
      (fVar2 * local_40 - fVar4 * (*(float *)param_2 - *(float *)param_1)) *
      *(float *)((int)param_5 + 4) < (float)_DAT_005d87b0) {
    return 0;
  }
  local_2c = *(float *)((int)param_3 + 4) - *(float *)((int)param_1 + 4);
  local_28 = *(float *)((int)param_3 + 8) - *(float *)((int)param_1 + 8);
  local_3c = *(float *)((int)param_4 + 4) - *(float *)((int)param_3 + 4);
  local_38 = *(float *)((int)param_4 + 8) - *(float *)((int)param_3 + 8);
  Vec3__SetXYZ();
  if (local_30 * *(float *)param_5 +
      local_28 * *(float *)((int)param_5 + 8) + local_2c * *(float *)((int)param_5 + 4) <
      (float)_DAT_005d87b0) {
    return 0;
  }
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__Cross(local_20,local_10,&local_40,unaff_EDI);
  dVar5 = Vec3__Dot(param_5,local_10,unaff_EDI);
  if (dVar5 < _DAT_005d87b0) {
    return 0;
  }
  return 1;
}
