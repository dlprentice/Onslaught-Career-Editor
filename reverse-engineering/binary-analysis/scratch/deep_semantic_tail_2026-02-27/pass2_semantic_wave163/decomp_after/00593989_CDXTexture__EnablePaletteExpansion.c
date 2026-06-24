/* address: 0x00593989 */
/* name: CDXTexture__EnablePaletteExpansion */
/* signature: void __stdcall CDXTexture__EnablePaletteExpansion(int param_1) */


void CDXTexture__EnablePaletteExpansion(int param_1)

{
  *(byte *)(param_1 + 0x61) = *(byte *)(param_1 + 0x61) | 0x10;
  return;
}
