/* address: 0x0055dc8a */
/* name: CRT__EhVectorConstructorIterator_Unwind */
/* signature: void CRT__EhVectorConstructorIterator_Unwind(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__EhVectorConstructorIterator_Unwind(void)

{
  int unaff_EBP;

  if (*(int *)(unaff_EBP + -0x20) == 0) {
    eh_vector_destructor_iterator
              (*(void **)(unaff_EBP + 8),*(int *)(unaff_EBP + 0xc),*(int *)(unaff_EBP + -0x1c),
               *(void **)(unaff_EBP + 0x18));
  }
  return;
}
