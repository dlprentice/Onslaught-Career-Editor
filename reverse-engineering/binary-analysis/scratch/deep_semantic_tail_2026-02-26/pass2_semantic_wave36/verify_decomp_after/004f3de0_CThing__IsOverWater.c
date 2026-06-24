/* address: 0x004f3de0 */
/* name: CThing__IsOverWater */
/* signature: int __fastcall CThing__IsOverWater(int param_1) */


int __fastcall CThing__IsOverWater(int param_1)

{
  float fVar1;
  double dVar2;

  fVar1 = DAT_006fbdfc;
  dVar2 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(param_1 + 0x1c));
  if ((double)fVar1 < dVar2) {
    return 1;
  }
  return 0;
}
