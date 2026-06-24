/* address: 0x00452fd0 */
/* name: CFEPMultiplayerStart__RenderSelectionBrackets */
/* signature: void __stdcall CFEPMultiplayerStart__RenderSelectionBrackets(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFEPMultiplayerStart__RenderSelectionBrackets(float param_1)

{
  int iVar1;
  float10 extraout_ST0;
  undefined4 local_c;
  undefined4 local_8;

  CPDSimpleSprite__Helper_0055e3ea();
  iVar1 = 4;
  local_c = (float)((float10)_DAT_005db1dc - extraout_ST0);
  local_8 = (int)(longlong)ROUND(param_1 * _DAT_005d8c70);
  do {
    CDXSurf__RenderSurface
              (0x42ac0000,local_c,0x3f666666,DAT_0089d7f0,local_8 * 0x3f0000 | 0xffffff,0x3f000000,
               0x3f000000,4,0,0x3f800000,0);
    local_c = local_c + _DAT_005db3dc;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  return;
}
