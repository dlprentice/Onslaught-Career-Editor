/* address: 0x00450400 */
/* name: CFEPBEConfig__PushProjectionMatrixForRender */
/* signature: void CFEPBEConfig__PushProjectionMatrixForRender(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFEPBEConfig__PushProjectionMatrixForRender(void)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  puVar2 = &DAT_009c6994;
  puVar3 = &DAT_006776f8;
  for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  CDXEngine__SetProjectionMatrix(&DAT_009c65c0,1.0,7000.0,1.0,0.75);
  return;
}
