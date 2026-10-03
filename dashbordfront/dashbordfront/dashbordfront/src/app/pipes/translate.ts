import { Pipe, PipeTransform, inject } from '@angular/core';
import { TranslationService } from '../services/translation';

@Pipe({
  name: 'translate',
  standalone: true,
  pure: false // impure : se réévalue à chaque cycle de détection de changement,
              // donc réagit immédiatement quand la langue change via le signal.
})
export class TranslatePipe implements PipeTransform {
  private translationService = inject(TranslationService);

  transform(key: string): string {
    return this.translationService.translate(key);
  }
}
