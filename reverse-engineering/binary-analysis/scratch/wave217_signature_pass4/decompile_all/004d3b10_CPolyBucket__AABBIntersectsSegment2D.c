/* address: 0x004d3b10 */
/* name: CPolyBucket__AABBIntersectsSegment2D */
/* signature: int __cdecl CPolyBucket__AABBIntersectsSegment2D(float rect_x, float rect_y, float rect_w, float rect_h, float * seg_p0, float * seg_p1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl
CPolyBucket__AABBIntersectsSegment2D
          (float rect_x,float rect_y,float rect_w,float rect_h,float *seg_p0,float *seg_p1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;

  fVar1 = rect_x + rect_w;
  if ((fVar1 < *seg_p0) && (fVar1 < *seg_p1)) {
    return 0;
  }
  if ((*seg_p0 < rect_x) && (*seg_p1 < rect_x)) {
    return 0;
  }
  fVar2 = rect_y + rect_h;
  if ((fVar2 < seg_p0[1]) && (fVar2 < seg_p1[1])) {
    return 0;
  }
  if ((seg_p0[1] < rect_y) && (seg_p1[1] < rect_y)) {
    return 0;
  }
  fVar3 = *seg_p1 - *seg_p0;
  fVar4 = seg_p1[1] - seg_p0[1];
  if (fVar3 != (float)_DAT_005d87b0) {
    fVar6 = (rect_x - *seg_p0) * (fVar4 / fVar3) + seg_p0[1];
    fVar5 = (fVar1 - *seg_p0) * (fVar4 / fVar3) + seg_p0[1];
    if ((fVar2 <= fVar6) && (fVar2 <= fVar5)) {
      return 0;
    }
    if ((fVar6 < rect_y) && (fVar5 < rect_y)) {
      return 0;
    }
  }
  if (fVar4 != (float)_DAT_005d87b0) {
    fVar5 = (rect_y - seg_p0[1]) * (fVar3 / fVar4) + *seg_p0;
    fVar2 = (fVar2 - seg_p0[1]) * (fVar3 / fVar4) + *seg_p0;
    if ((fVar1 <= fVar5) && (fVar1 <= fVar2)) {
      return 0;
    }
    if ((fVar5 < rect_x) && (fVar2 < rect_x)) {
      return 0;
    }
  }
  return 1;
}
