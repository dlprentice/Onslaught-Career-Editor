/* address: 0x00441490 */
/* name: CDXEngine__UpdateWrappedThingPositionsAndDistance */
/* signature: void __cdecl CDXEngine__UpdateWrappedThingPositionsAndDistance(float param_1, float param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl
CDXEngine__UpdateWrappedThingPositionsAndDistance(float param_1,float param_2,float param_3)

{
  float *pfVar1;
  int *piVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  bool bVar7;
  double dVar8;

  piVar2 = DAT_0066eb78;
  do {
    if (piVar2 == (int *)0x0) {
      return;
    }
    fVar4 = (float)piVar2[7] - param_1;
    pfVar1 = (float *)(piVar2 + 7);
    fVar3 = (float)piVar2[8] - param_2;
    piVar2[0x20] = (int)SQRT((*pfVar1 - param_1) * (*pfVar1 - param_1) +
                             ((float)piVar2[8] - param_2) * ((float)piVar2[8] - param_2) +
                             ((float)piVar2[9] - param_3) * ((float)piVar2[9] - param_3));
    fVar6 = _DAT_006282fc;
    if (_DAT_006282fc < fVar4) {
      *pfVar1 = *pfVar1 - (_DAT_006282fc + _DAT_006282fc);
    }
    fVar5 = -_DAT_006282fc;
    if (fVar4 < fVar5) {
      *pfVar1 = _DAT_006282fc + _DAT_006282fc + *pfVar1;
    }
    bVar7 = _DAT_006282fc < fVar3;
    if (bVar7) {
      piVar2[8] = (int)((float)piVar2[8] - (_DAT_006282fc + _DAT_006282fc));
    }
    if (-_DAT_006282fc <= fVar3) {
      if (bVar7 || (fVar4 < fVar5 || fVar6 < fVar4)) goto LAB_0044156e;
    }
    else {
      piVar2[8] = (int)(_DAT_006282fc + _DAT_006282fc + (float)piVar2[8]);
LAB_0044156e:
      dVar8 = CStaticShadows__Helper_0047eb80(0x6fadc8,pfVar1);
      piVar2[9] = (int)(float)dVar8;
      (**(code **)(*piVar2 + 0x50))(pfVar1);
      if ((piVar2[6] != -1) && (piVar2 != (int *)0xfffffff4)) {
        CMapWhoEntry__UpdatePosition(pfVar1);
      }
    }
    piVar2 = (int *)piVar2[0x1f];
  } while( true );
}
