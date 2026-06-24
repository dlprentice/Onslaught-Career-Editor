/* address: 0x004cb080 */
/* name: CParticleManager__Unk_004cb080 */
/* signature: void CParticleManager__Unk_004cb080(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CParticleManager__Unk_004cb080(void)

{
  undefined4 *puVar1;

  for (puVar1 = DAT_0082b3e8; puVar1 != (undefined4 *)0x0; puVar1 = (undefined4 *)*puVar1) {
    if ((puVar1[1] != 0) && (*(int *)(puVar1[1] + 0xa4) == 0)) {
      puVar1[1] = 0;
    }
  }
  return;
}
