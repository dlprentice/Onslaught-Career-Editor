/* address: 0x004ebbc0 */
/* name: CGame__InitStaticShadowBuildState */
/* signature: void __fastcall CGame__InitStaticShadowBuildState(int param_1) */


void __fastcall CGame__InitStaticShadowBuildState(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  CConsole__RegisterCommand
            (s_BuildStaticShadows_00632974,s_Force_a__re_build_of_the_static_s_00632988,
             &LAB_004ebbb0,0);
  puVar2 = (undefined4 *)(param_1 + 0x18);
  for (iVar1 = 0x1000; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)(param_1 + 0x4018) = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}
