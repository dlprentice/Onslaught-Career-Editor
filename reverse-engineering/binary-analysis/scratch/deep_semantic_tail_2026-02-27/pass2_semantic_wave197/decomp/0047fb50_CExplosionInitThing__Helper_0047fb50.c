/* address: 0x0047fb50 */
/* name: CExplosionInitThing__Helper_0047fb50 */
/* signature: void __cdecl CExplosionInitThing__Helper_0047fb50(int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CExplosionInitThing__Helper_0047fb50(int param_1,int param_2,int param_3)

{
  int iVar1;
  void *pvVar2;
  int *extraout_ECX;
  int *piVar3;
  short *psVar4;
  int unaff_EDI;
  short *psVar5;
  float y;
  float z;
  float scale_x;
  float scale_y;
  short *psVar6;
  undefined1 *puVar7;
  short *text;
  float transition;
  float fVar8;
  int *piVar9;
  int fade_out;

  CRT__AllocaProbe();
  D3DStateCache__SetState114Raw(0,6,2);
  D3DStateCache__SetState114Raw(0,5,2);
  D3DStateCache__SetStateCached(0,1,4);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  param_1 = 0x42480000;
  param_2 = 2;
  piVar9 = extraout_ECX;
  do {
    piVar3 = piVar9 + 3;
    if (*piVar3 != 0) {
      psVar5 = (short *)(DAT_00672fd0 - (float)piVar9[2]);
      if ((float)psVar5 <= _DAT_005d857c) {
        if (_DAT_005dbe00 <= (float)psVar5) {
          psVar5 = (short *)(((float)psVar5 - _DAT_005dbdfc) * _DAT_005d8c44);
        }
        else if ((float)_DAT_005d87e0 < (float)psVar5) {
          psVar5 = (short *)0x3f800000;
        }
        pvVar2 = (void *)piVar9[1];
        fVar8 = 550.0;
        puVar7 = &stack0x00000014;
        CPlatform__Font(&DAT_0088a0a8,0);
        iVar1 = CFEPLanguageTest__Helper_00465a20(puVar7,pvVar2,fVar8);
        if ((CAREER_mControllerConfig_P1 == 3) || (CAREER_mControllerConfig_P1 == 4)) {
          pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
          *(undefined4 *)((int)pvVar2 + 0x16c) = 1;
        }
        if (0 < iVar1) {
          psVar4 = (short *)&stack0x00000014;
          do {
            piVar9 = &param_3;
            psVar6 = psVar4;
            pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
            CDXFont__GetTextExtent(pvVar2,psVar6,piVar9);
            fade_out = 0;
            transition = 1.4013e-45;
            scale_y = -NAN;
            scale_x = 1.0;
            z = 1.0;
            y = 1.0;
            pvVar2 = (void *)((_DAT_008aa4e8 * _DAT_005d85ec + _DAT_008aa4f0) -
                             (float)param_3 * _DAT_005d85ec);
            fVar8 = (float)param_1;
            psVar6 = psVar4;
            text = psVar5;
            CPlatform__Font(&DAT_0088a0a8,0);
            CDXFont__DrawTextDynamic
                      (pvVar2,fVar8,y,z,scale_x,scale_y,(int)psVar6,text,transition,fade_out,
                       unaff_EDI);
            param_1 = (int)((float)param_1 + _DAT_005db2b8);
            psVar4 = psVar4 + 100;
            iVar1 = iVar1 + -1;
          } while (iVar1 != 0);
        }
        pvVar2 = CPlatform__Font(&DAT_0088a0a8,0);
        *(undefined4 *)((int)pvVar2 + 0x16c) = 0;
      }
      else {
        *piVar3 = 0;
      }
    }
    param_2 = param_2 + -1;
    piVar9 = piVar3;
  } while (param_2 != 0);
  return;
}
