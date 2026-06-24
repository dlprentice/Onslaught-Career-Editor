/* address: 0x00472e50 */
/* name: CVBufTexture__Helper_00472e50 */
/* signature: int CVBufTexture__Helper_00472e50(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CVBufTexture__Helper_00472e50(void)

{
  int *tex;
  int extraout_EAX;
  int in_ECX;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000014;

  tex = *(int **)(in_ECX + 8);
  if (tex == (int *)0x0) {
    if ((DAT_0089ce84 == (int *)0x0) &&
       (DAT_0089ce84 = CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1),
       DAT_0089ce84 == (int *)0x0)) {
      return 0;
    }
    in_stack_00000014 = -1.7014118e+38;
    tex = DAT_0089ce84;
  }
  CVBufTexture__DrawSpriteEx
            (in_stack_00000004,in_stack_00000008,0.001,tex,4,0,1.0,0.0,in_stack_00000014,
             in_stack_0000000c / (float)tex[0x2b],in_stack_00000010 / (float)(int)(short)tex[0x2c],
             0.0,_DAT_005d8568 / in_stack_0000000c + _DAT_005d8568,0.0,
             _DAT_005d8568 / in_stack_00000010 + _DAT_005d8568);
  return extraout_EAX;
}
