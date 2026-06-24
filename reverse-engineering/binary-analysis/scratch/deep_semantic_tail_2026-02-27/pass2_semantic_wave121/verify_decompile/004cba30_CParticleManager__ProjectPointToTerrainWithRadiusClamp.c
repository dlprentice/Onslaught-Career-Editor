/* address: 0x004cba30 */
/* name: CParticleManager__ProjectPointToTerrainWithRadiusClamp */
/* signature: int __stdcall CParticleManager__ProjectPointToTerrainWithRadiusClamp(void * param_1, float param_2, void * param_3) */


int CParticleManager__ProjectPointToTerrainWithRadiusClamp
              (void *param_1,float param_2,void *param_3)

{
  double dVar1;

  dVar1 = CStaticShadows__Helper_0047eb80(0x6fadc8,param_1);
  if ((float)dVar1 < param_2 + *(float *)((int)param_1 + 8)) {
    *(undefined4 *)param_3 = *(undefined4 *)param_1;
    *(undefined4 *)((int)param_3 + 4) = *(undefined4 *)((int)param_1 + 4);
    *(undefined4 *)((int)param_3 + 8) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)param_3 + 0xc) = *(undefined4 *)((int)param_1 + 0xc);
    *(float *)((int)param_3 + 8) = (float)dVar1 - param_2;
    return 1;
  }
  return 0;
}
